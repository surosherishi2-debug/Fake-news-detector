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
    this.animationFrame = null;
    this.hoveredNode = null;

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());

    this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
  }

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height || 420;
    this.draw();
  }

  loadCascade(cascadeData) {
    if (!this.canvas) return;
    const w = this.canvas.width;
    const h = this.canvas.height;
    const cx = w / 2;
    const cy = h / 2;

    this.nodes = [];
    this.edges = cascadeData.edges || [];

    // Layout nodes algorithmically
    const rawNodes = cascadeData.nodes || [];
    rawNodes.forEach((n, idx) => {
      let x, y, color, radius;
      if (n.type === 'article') {
        x = cx;
        y = cy;
        color = '#5E4BF5';
        radius = 24;
      } else if (n.type === 'publisher') {
        x = cx - 180;
        y = cy - 80;
        color = '#38BDF8';
        radius = 18;
      } else if (n.id.includes('bot')) {
        // Cluster bots on the right side in tight ring
        const angle = (idx * 1.2);
        x = cx + 160 + Math.cos(angle) * 60;
        y = cy + Math.sin(angle) * 70;
        color = '#EF4444';
        radius = 12;
      } else if (n.verified) {
        x = cx - 120;
        y = cy + 100;
        color = '#10B981';
        radius = 16;
      } else {
        x = cx + (idx % 2 === 0 ? -90 : 90);
        y = cy - 130;
        color = '#94A3B8';
        radius = 13;
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

    this.startAnimation();
  }

  handleMouseMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    this.hoveredNode = null;
    for (const node of this.nodes) {
      const dist = Math.hypot(node.x - mouseX, node.y - mouseY);
      if (dist < node.radius + 4) {
        this.hoveredNode = node;
        break;
      }
    }
    this.draw();
  }

  startAnimation() {
    let t = 0;
    const animate = () => {
      t += 0.03;
      // Slight floating motion
      this.nodes.forEach((n, idx) => {
        if (n.type !== 'article') {
          n.dy = Math.sin(t + idx) * 0.4;
        } else {
          n.dy = 0;
        }
      });
      this.draw();
      this.animationFrame = requestAnimationFrame(animate);
    };
    if (this.animationFrame) cancelAnimationFrame(this.animationFrame);
    animate();
  }

  draw() {
    if (!this.ctx) return;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw Edges
    this.edges.forEach((edge) => {
      const src = this.nodes.find((n) => n.id === edge.source);
      const tgt = this.nodes.find((n) => n.id === edge.target);
      if (src && tgt) {
        ctx.beginPath();
        ctx.moveTo(src.x, src.y + (src.dy || 0));
        ctx.lineTo(tgt.x, tgt.y + (tgt.dy || 0));

        if (src.id.includes('bot') || tgt.id.includes('bot')) {
          ctx.strokeStyle = 'rgba(239, 68, 68, 0.45)';
          ctx.setLineDash([4, 4]);
          ctx.lineWidth = 2;
        } else {
          ctx.strokeStyle = 'rgba(165, 180, 252, 0.25)';
          ctx.setLineDash([]);
          ctx.lineWidth = 1.5;
        }
        ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // Draw Nodes
    this.nodes.forEach((node) => {
      const ny = node.y + (node.dy || 0);

      // Pulsing outer halo for bot nodes
      if (node.id.includes('bot')) {
        ctx.beginPath();
        ctx.arc(node.x, ny, node.radius + 6, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(239, 68, 68, 0.15)';
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(node.x, ny, node.radius, 0, Math.PI * 2);
      ctx.fillStyle = node.color;
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();

      // Label
      ctx.font = '11px sans-serif';
      ctx.fillStyle = '#E2E8F0';
      ctx.textAlign = 'center';
      ctx.fillText(node.name, node.x, ny + node.radius + 14);
    });

    // Tooltip for hovered node
    if (this.hoveredNode) {
      const n = this.hoveredNode;
      const ny = n.y + (n.dy || 0);
      const tipText = `${n.name} (${n.type.toUpperCase()}) | Followers: ${n.followers.toLocaleString()}`;

      ctx.font = '12px sans-serif';
      const textWidth = ctx.measureText(tipText).width;

      ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
      ctx.beginPath();
      ctx.roundRect(n.x - textWidth / 2 - 10, ny - n.radius - 32, textWidth + 20, 24, 6);
      ctx.fill();

      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.fillText(tipText, n.x, ny - n.radius - 16);
    }
  }
}

window.CascadeGraphVisualizer = CascadeGraphVisualizer;
