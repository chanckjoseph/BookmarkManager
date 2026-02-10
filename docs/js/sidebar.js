
// Docs Sidebar Component
// Usage: Include this script and <nav id="sidebar-container"></nav> in your HTML.

const SIDEBAR_CONFIG = [
    {
        title: "Docs Hub",
        path: "index.html",
        isHeader: true
    },
    {
        category: "Primary Actions",
        links: [
            { text: "🚀 Launch Application", path: "/dashboard", isButton: true, isExternal: true }
        ]
    },
    {
        category: "Architecture",
        links: [
            { text: "Implementation Plan", path: "arch/plan.html" },
            { text: "Sync Logic Spec", path: "arch/sync_logic.html" }
        ]
    },
    {
        category: "Team & Process",
        links: [
            { text: "Multi-Agent Workflow", path: "process/workflow.html" }
        ]
    },
    {
        category: "History & Sprints",
        links: [
            { text: "Sprint 01: Feasibility", path: "sprints/sprint-01/index.html" },
            { text: "Sprint 02: MVP Core", path: "sprints/sprint-02/index.html" },
            { text: "Sprint 03: Persistence", path: "sprints/sprint-03/index.html" },
            { text: "Sprint 04: Organization", path: "sprints/sprint-04/index.html" },
            { text: "Sprint 05: UX & Perf", path: "sprints/sprint-05/index.html" }
        ]
    }
];

function renderSidebar() {
    const container = document.querySelector('.sidebar');
    if (!container) return;

    // Detect depth to docs root
    const pathParts = window.location.pathname.split('/');
    const docsIndex = pathParts.indexOf('docs');
    const depth = docsIndex !== -1 ? pathParts.length - docsIndex - 2 : 0;
    const prefix = '../'.repeat(Math.max(0, depth));

    let html = '';

    // Render Navigation Links
    SIDEBAR_CONFIG.forEach(item => {
        if (item.isHeader && item.title) {
            html += `<h1 style="margin-bottom:2rem;"><a href="${prefix}${item.path}" style="color:white; text-decoration:none;">${item.title}</a></h1>`;
        } else if (item.category) {
            html += `<h3>${item.category}</h3><ul>`;
            item.links.forEach(link => {
                const fullPath = link.isExternal ? link.path : prefix + link.path;
                const isActive = !link.isExternal && window.location.pathname.endsWith(link.path);
                const activeClass = isActive ? 'class="active"' : '';
                const btnClass = link.isButton ? 'class="btn-nav"' : '';

                html += `<li><a href="${fullPath}" ${activeClass} ${btnClass}>${link.text}</a></li>`;
            });
            html += `</ul>`;
        }
    });

    // Add Global Sidebar Footer
    const today = new Date().toISOString().split('T')[0];
    html += `
    <div style="margin-top: auto; padding-top: 2rem; font-size: 0.75rem; color: var(--text-dim); border-top: 1px solid var(--glass-border);">
        <p>&copy; 2026 BM Team</p>
        <p><strong>Updated:</strong> ${today}</p>
    </div>`;

    container.innerHTML = html;
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
}

document.addEventListener('DOMContentLoaded', renderSidebar);
