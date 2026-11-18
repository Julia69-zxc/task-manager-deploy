const list = document.querySelector("#tasks");
const form = document.querySelector("#task-form");
const input = document.querySelector("#task-title");
const counter = document.querySelector("#counter");
const message = document.querySelector("#message");

async function api(path, options={}) {
  const response = await fetch(`/api${path}`, {
    headers: {"Content-Type":"application/json", ...(options.headers||{})},
    ...options
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Ошибка ${response.status}`);
  return data;
}
function showError(error){ message.textContent = error.message; }
async function loadTasks(){
  try {
    message.textContent = "";
    const tasks = await api("/tasks");
    list.replaceChildren();
    tasks.forEach(task => {
      const li = document.createElement("li");
      if(task.done) li.classList.add("done");
      const toggle = document.createElement("button");
      toggle.className="check"; toggle.textContent=task.done?"✓":"○";
      toggle.setAttribute("aria-label","Изменить статус");
      toggle.onclick=async()=>{try{await api(`/tasks/${task.id}`,{method:"PATCH",body:JSON.stringify({done:!task.done})});loadTasks()}catch(e){showError(e)}};
      const title=document.createElement("span"); title.textContent=task.title;
      const del=document.createElement("button"); del.className="delete"; del.textContent="Удалить";
      del.onclick=async()=>{try{await api(`/tasks/${task.id}`,{method:"DELETE"});loadTasks()}catch(e){showError(e)}};
      li.append(toggle,title,del); list.append(li);
    });
    counter.textContent=`Всего задач: ${tasks.length} · Выполнено: ${tasks.filter(t=>t.done).length}`;
  } catch(e){showError(e);counter.textContent="Нет соединения с API";}
}
form.addEventListener("submit",async e=>{
  e.preventDefault(); const title=input.value.trim(); if(!title)return;
  try{await api("/tasks",{method:"POST",body:JSON.stringify({title})});input.value="";await loadTasks()}catch(err){showError(err)}
});
document.querySelector("#refresh").addEventListener("click",loadTasks);
loadTasks();
