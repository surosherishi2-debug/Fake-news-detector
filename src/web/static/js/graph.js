/**
 * Interactive 2D Social Propagation Cascade Visualizer.
 * Renders heterogeneous Article, User, Publisher, and Botnet nodes on HTML5 Canvas.
 */

class CascadeGraphVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.nodes = [];
    this.edges = [];
    this.hoveredNode = null;
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
  }

  resizeCanvas() {
    if (!this.canvas || !this.canvas.parentElement) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.width = rect.width || 640;
    this.height = rect.height || 460;
    this.canvas.width = this.width * this.dpr;
    this.canvas.height = this.height * this.dpr;
    this.canvas.style.width = `${this.width}px`;
    this.canvas.style.height = `${this.height}px`;
    this.draw();
  }

  renderCascade(cascadeData) {
    this.loadCascade(cascadeData);
  }

  loadCascade(cascadeData) {
    if (!this.canvas) return;
    const w = this.width || this.canvas.clientWidth || 640;
    const h = this.height || this.canvas.clientHeight || 460;
    const cx = w / 2;
    const cy = h / 2;

    this.nodes = [];
    this.edges = cascadeData.edges || [];

    const rawNodes = cascadeData.nodes || [];
    rawNodes.forEach((n, idx) => {
      let x, y, color, radius;
      if (n.type === 'article') {
        x = cx;
        y = cy;
        color = '#3b82f6';
        radius = 22;
      } else if (n.type === 'publisher') {
        x = cx - 180;
        y = cy - 80;
        color = '#a1a1aa';
        radius = 16;
      } else if (n.id.includes('bot')) {
        const angle = idx * 1.2;
        x = cx + 160 + Math.cos(angle) * 60;
        y = cy + Math.sin(angle) * 70;
        color = '#e5484d';
        radius = 12;
      } else if (n.verified) {
        x = cx - 120;
        y = cy + 100;
        color = '#4cc38a';
        radius = 15;
      } else {
        x = cx + (idx % 2 === 0 ? -90 : 90);
        y = cy - 130;
        color = '#737373';
        radius = 12;
      }

      this.nodes.push({
        id: n.id,
        name: n.name || n.id,
        type: n.type,
        verified: n.verified,
        followers: n.follower_count || 0,
        x,
        y,
        color,
        radius,
      });
    });

    this.draw();
  }

  handleMouseMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    let nextHover = null;
    for (const node of this.nodes) {
      const dist = Math.hypot(node.x - mouseX, node.y - mouseY);
      if (dist < node.radius + 6) {
        nextHover = node;
        break;
      }
    }
    if (nextHover !== this.hoveredNode) {
      this.hoveredNode = nextHover;
      this.canvas.style.cursor = nextHover ? 'pointer' : 'default';
      this.draw();
    }
  }

  draw() {
    if (!this.ctx) return;
    const ctx = this.ctx;
    ctx.save();
    ctx.scale(this.dpr, this.dpr);
    ctx.clearRect(0, 0, this.width, this.height);

    // Draw Edges
    this.edges.forEach((edge) => {
      const src = this.nodes.find((n) => n.id === edge.source);
      const tgt = this.nodes.find((n) => n.id === edge.target);
      if (src && tgt) {
        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);

        if (src.id.includes('bot') || tgt.id.includes('bot')) {
          ctx.strokeStyle = 'rgba(229, 72, 77, 0.45)';
          ctx.setLineDash([4, 4]);
          ctx.lineWidth = 1.5;
        } else {
          ctx.strokeStyle = 'rgba(161, 161, 170, 0.25)';
          ctx.setLineDash([]);
          ctx.lineWidth = 1.25;
        }
        ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // Draw Nodes
    this.nodes.forEach((node) => {
      const isHovered = this.hoveredNode && this.hoveredNode.id === node.id;

      if (node.id.includes('bot')) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + 5, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(229, 72, 77, 0.14)';
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      ctx.fillStyle = node.color;
      ctx.fill();
      ctx.lineWidth = isHovered ? 2.5 : 1.5;
      ctx.strokeStyle = isHovered ? '#ffffff' : '#141415';
      ctx.stroke();

      ctx.font = '11px "IBM Plex Sans", sans-serif';
      ctx.fillStyle = '#a1a1a6';
      ctx.textAlign = 'center';
      ctx.fillText(node.name, node.x, node.y + node.radius + 14);
    });

    // Tooltip for hovered node
    if (this.hoveredNode) {
      const n = this.hoveredNode;
      const tipText = `${n.name} (${n.type}) · ${n.followers.toLocaleString()} followers`;

      ctx.font = '12px "JetBrains Mono", monospace';
      const textWidth = ctx.measureText(tipText).width;
      const boxW = textWidth + 16;
      const boxX = Math.max(8, Math.min(this.width - boxW - 8, n.x - boxW / 2));
      const boxY = Math.max(8, n.y - n.radius - 34);

      ctx.fillStyle = '#232325';
      ctx.strokeStyle = 'rgba(237, 237, 237, 0.14)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(boxX, boxY, boxW, 24, 6);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#ededed';
      ctx.textAlign = 'center';
      ctx.fillText(tipText, boxX + boxW / 2, boxY + 16);
    }

    ctx.restore();
  }
}

window.CascadeGraphVisualizer = CascadeGraphVisualizer;
window.CascadeVisualizer = CascadeGraphVisualizer;
