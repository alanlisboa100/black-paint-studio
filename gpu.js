/**
 * Acabamento GPU leve (WebGL, powerPreference: low-power).
 * Um passe sob demanda — não roda a cada pincelada e não carrega modelo de imagem.
 */
(function (root) {
  function detect() {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl2', { premultipliedAlpha: false, antialias: false, powerPreference: 'low-power' })
        || canvas.getContext('webgl', { premultipliedAlpha: false, antialias: false, powerPreference: 'low-power' });
      if (!gl) return { available: false, api: 'none', renderer: '' };
      const info = gl.getExtension('WEBGL_debug_renderer_info');
      return {
        available: true,
        api: typeof WebGL2RenderingContext !== 'undefined' && gl instanceof WebGL2RenderingContext ? 'webgl2' : 'webgl',
        renderer: info ? String(gl.getParameter(info.UNMASKED_RENDERER_WEBGL) || '') : ''
      };
    } catch {
      return { available: false, api: 'none', renderer: '' };
    }
  }

  const VERT = `
    attribute vec2 a_pos;
    varying vec2 v_uv;
    void main() {
      v_uv = a_pos * 0.5 + 0.5;
      gl_Position = vec4(a_pos, 0.0, 1.0);
    }
  `;
  const FRAG = `
    precision mediump float;
    varying vec2 v_uv;
    uniform sampler2D u_image;
    uniform vec2 u_texel;
    uniform float u_grain;
    uniform float u_sharpen;
    float hash(vec2 p) {
      return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
    }
    void main() {
      vec4 c = texture2D(u_image, v_uv);
      vec4 n = texture2D(u_image, v_uv + vec2(0.0, u_texel.y));
      vec4 s = texture2D(u_image, v_uv - vec2(0.0, u_texel.y));
      vec4 e = texture2D(u_image, v_uv + vec2(u_texel.x, 0.0));
      vec4 w = texture2D(u_image, v_uv - vec2(u_texel.x, 0.0));
      vec4 blur = (n + s + e + w) * 0.25;
      vec3 sharp = c.rgb + (c.rgb - blur.rgb) * u_sharpen;
      float g = (hash(v_uv * 900.0) - 0.5) * u_grain;
      gl_FragColor = vec4(clamp(sharp + g, 0.0, 1.0), c.a);
    }
  `;

  function compile(gl, type, src) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, src);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      gl.deleteShader(shader);
      throw new Error('shader');
    }
    return shader;
  }

  function applyFinish(sourceCanvas, options) {
    const info = detect();
    if (!info.available) throw new Error('WebGL indisponível neste navegador.');
    const grain = Math.min(0.08, Math.max(0, Number(options?.grain) || 0.028));
    const sharpen = Math.min(0.7, Math.max(0, Number(options?.sharpen) || 0.22));
    const glCanvas = document.createElement('canvas');
    const maxEdge = 1440;
    const scale = Math.min(1, maxEdge / Math.max(sourceCanvas.width, sourceCanvas.height));
    glCanvas.width = Math.max(1, Math.round(sourceCanvas.width * scale));
    glCanvas.height = Math.max(1, Math.round(sourceCanvas.height * scale));
    const gl = glCanvas.getContext('webgl', { premultipliedAlpha: false, antialias: false, powerPreference: 'low-power', preserveDrawingBuffer: true });
    if (!gl) throw new Error('WebGL indisponível neste navegador.');
    const program = gl.createProgram();
    gl.attachShader(program, compile(gl, gl.VERTEX_SHADER, VERT));
    gl.attachShader(program, compile(gl, gl.FRAGMENT_SHADER, FRAG));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error('programa GPU');
    gl.useProgram(program);
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(program, 'a_pos');
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, sourceCanvas);
    gl.uniform1i(gl.getUniformLocation(program, 'u_image'), 0);
    gl.uniform2f(gl.getUniformLocation(program, 'u_texel'), 1 / glCanvas.width, 1 / glCanvas.height);
    gl.uniform1f(gl.getUniformLocation(program, 'u_grain'), grain);
    gl.uniform1f(gl.getUniformLocation(program, 'u_sharpen'), sharpen);
    gl.viewport(0, 0, glCanvas.width, glCanvas.height);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    const result = document.createElement('canvas');
    result.width = glCanvas.width; result.height = glCanvas.height;
    result.getContext('2d').drawImage(glCanvas, 0, 0);
    gl.deleteTexture(texture); gl.deleteBuffer(buffer);
    for (const shader of gl.getAttachedShaders(program) || []) gl.deleteShader(shader);
    gl.deleteProgram(program);
    gl.getExtension('WEBGL_lose_context')?.loseContext();
    return result;
  }

  root.PaintGPU = { detect, applyFinish };
})(typeof window !== 'undefined' ? window : globalThis);
