document.addEventListener('DOMContentLoaded', function () {
    var tasks = document.querySelectorAll('.task');
    var taskLists = document.querySelectorAll('.task-list');

    tasks.forEach(function (task) {
        task.draggable = true;

        task.addEventListener('dragstart', function (e) {
            e.dataTransfer.setData('text/plain', task.dataset.taskId);
        });
    });

    taskLists.forEach(function (list) {
        list.addEventListener('dragover', function (e) {
            e.preventDefault();
        });

        list.addEventListener('drop', function (e) {
            e.preventDefault();
            var taskId = e.dataTransfer.getData('text/plain');
            var task = document.querySelector(`[data-task-id='${taskId}']`);
            list.appendChild(task);

            // Update task category via AJAX
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/update_task_category', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({
                taskId: taskId,
                category: list.id.replace('-', ' ')
            }));
        });
    });
});
