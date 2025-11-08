async function fetchTasks() {
  const r = await fetch('/merge', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
  if (r.ok) {
    const json = await r.json();
    return json.tasks || [];
  }
  return [];
}

function renderTasks(tasks) {
  const ul = document.getElementById('tasks');
  ul.innerHTML = '';
  if (!Array.isArray(tasks)) return;
  tasks.forEach(t => {
    const li = document.createElement('li');
    li.className = 'task';
    li.textContent = t.title || '(no title)';
    ul.appendChild(li);
  });
}

async function addTask(task) {
  const payload = { userInput: { task } };
  const r = await fetch('/add', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!r.ok) throw new Error('failed to add');
  const json = await r.json();
  return json.tasks || [];
}

document.getElementById('addForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const input = document.getElementById('taskInput');
  const val = input.value.trim();
  if (!val) return;
  try {
    const tasks = await addTask(val);
    renderTasks(tasks);
    input.value = '';
  } catch (err) {
    console.error(err);
    alert('Error adding task');
  }
});

// Initial load: fetch tasks
(async function() {
  try {
    const tasks = await fetchTasks();
    renderTasks(tasks);
  } catch (err) {
    console.error('failed to load tasks', err);
  }
})();
