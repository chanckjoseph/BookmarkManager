
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
            { text: "🚀 Launch Application", path: "../prototype/dashboard.html", isButton: true }
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
            { text: "Sprint 04: Organization", path: "sprints/sprint-04/index.html" }
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

    SIDEBAR_CONFIG.forEach(item => {
        if (item.isHeader && item.title) {
            html += `<h1><a href="${prefix}${item.path}" style="color:white; text-decoration:none;">${item.title}</a></h1>`;
        } else if (item.category) {
            html += `<h3>${item.category}</h3><ul>`;
            item.links.forEach(link => {
                const fullPath = prefix + link.path;
                const isActive = window.location.href.includes(link.path);
                const activeClass = isActive ? 'class="active"' : '';
                const btnClass = link.isButton ? 'class="btn-nav"' : '';

                html += `<li><a href="${fullPath}" ${activeClass} ${btnClass}>${link.text}</a></li>`;
            });
            html += `</ul>`;
        }
    });

    container.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', renderSidebar);
