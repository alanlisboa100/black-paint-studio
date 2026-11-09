/**
 * Bíblia da Misuki no cliente: eixos de construção e montagem de prompt.
 */
(function (root) {
  const DEFAULT_POSES = {
    front: 'retrato frontal da cintura para cima, ombros abertos, olhar na câmera',
    'three-quarter': 'três quartos, queixo levemente baixo, uma mecha atravessando o ombro',
    profile: 'perfil esquerdo, silhueta dos chifres e do nariz limpa',
    smile: 'mesmo retrato frontal, sorriso mínimo sem mostrar dentes',
    full: 'corpo inteiro em pé, botas plataforma, uma mão à frente'
  };

  function buildPrompt(card, pose) {
    const poses = card?.poses || DEFAULT_POSES;
    const chosen = poses[pose] || poses.front;
    const core = card?.promptCore || 'Anime girl named Misuki, BLACKCORE identity';
    const finish = card?.promptFinish || 'sharp lineart, dark atmosphere';
    const negative = card?.negative ? ` Avoid: ${card.negative}.` : '';
    return `${core}. Pose: ${chosen}. ${finish}.${negative}`;
  }

  function drawConstruction(ctx, width, height) {
    const cx = width / 2;
    const head = Math.min(width, height) * 0.22;
    const cy = height * 0.28;
    ctx.save();
    ctx.strokeStyle = '#c8ed4a';
    ctx.fillStyle = 'rgba(200, 237, 74, 0.06)';
    ctx.lineWidth = Math.max(1, width * 0.002);
    ctx.beginPath();
    ctx.arc(cx, cy, head, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx, cy - head);
    ctx.lineTo(cx, cy + head * 1.15);
    ctx.moveTo(cx - head, cy);
    ctx.lineTo(cx + head, cy);
    ctx.stroke();
    const jawY = cy + head * 0.72;
    ctx.beginPath();
    ctx.moveTo(cx - head * 0.62, cy + head * 0.18);
    ctx.quadraticCurveTo(cx, jawY + head * 0.28, cx + head * 0.62, cy + head * 0.18);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx - head * 0.42, cy + head * 0.08);
    ctx.quadraticCurveTo(cx - head * 0.18, cy + head * 0.14, cx - head * 0.08, cy + head * 0.1);
    ctx.moveTo(cx + head * 0.08, cy + head * 0.1);
    ctx.quadraticCurveTo(cx + head * 0.18, cy + head * 0.14, cx + head * 0.42, cy + head * 0.08);
    ctx.stroke();
    ctx.setLineDash([6, 6]);
    ctx.beginPath();
    ctx.moveTo(cx, cy + head * 1.1);
    ctx.lineTo(cx, height * 0.72);
    ctx.moveTo(cx - head * 1.1, height * 0.48);
    ctx.lineTo(cx + head * 1.1, height * 0.48);
    ctx.stroke();
    ctx.restore();
  }

  root.MisukiStudio = { buildPrompt, drawConstruction, DEFAULT_POSES };
})(typeof window !== 'undefined' ? window : globalThis);
