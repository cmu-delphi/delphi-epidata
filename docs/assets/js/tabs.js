// Simple Tab Switching Logic
function activateTab(clickedButton, container) {
    const buttons = container.querySelectorAll('.tab-header button');
    const contents = container.querySelectorAll('.tab-content');

    // Deactivate all
    buttons.forEach(btn => btn.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));

    // Activate clicked button
    clickedButton.classList.add('active');

    // Activate corresponding content
    const tabId = clickedButton.dataset.tab;
    const content = container.querySelector(`.tab-content[data-tab="${tabId}"]`);
    if (content) {
        content.classList.add('active');
    }
}

function initTabContainer(container) {
    const buttons = container.querySelectorAll('.tab-header button');
    buttons.forEach(button => {
        button.addEventListener('click', () => activateTab(button, container));
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const tabContainers = document.querySelectorAll('.code-tabs');
    tabContainers.forEach(initTabContainer);
});
