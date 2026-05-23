document.addEventListener("DOMContentLoaded",()=>{
  const t=document.getElementById("toggleTheme");
  if(localStorage.getItem("theme")==="dark")document.body.classList.add("dark");
  if(t)t.addEventListener("click",()=>{document.body.classList.toggle("dark");
    localStorage.setItem("theme",document.body.classList.contains("dark")?"dark":"light");});
});
