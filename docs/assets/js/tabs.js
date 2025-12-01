// Simple Tab Switching Logic
document.addEventListener('DOMContentLoaded', function () {
    const tabContainers = document.querySelectorAll('.code-tabs');

    tabContainers.forEach(container => {
        const headers = container.querySelector('.tab-header');
        const buttons = headers.querySelectorAll('button');
        const contents = container.querySelectorAll('.tab-content');

        buttons.forEach(button => {
            button.addEventListener('click', () => {
                buttons.forEach(btn => btn.classList.remove('active'));
                contents.forEach(content => content.classList.remove('active'));

                button.classList.add('active');

                const tabId = button.getAttribute('data-tab');
                const content = container.querySelector(`.tab-content[data-tab="${tabId}"]`);
                if (content) {
                    content.classList.add('active');
                }
            });
        });
    });
});
