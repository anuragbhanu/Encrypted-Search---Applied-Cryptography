async function searchKeyword(){
  const kw = document.getElementById("kw").value.trim();
  const out = document.getElementById("kw_results");
  out.innerHTML = "Searching...";
  const res = await fetch("/search/keyword", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({keyword: kw})});
  const j = await res.json();
  if(j.error){ out.innerHTML = "<b>Error:</b> "+j.error; return; }
  if(!j.results || j.results.length===0){ out.innerHTML = "<i>No results</i>"; return; }
  out.innerHTML = j.results.map(r=>`<div class="result"><b>${r.name}</b><div>${r.description}</div><div><i>${r.category}</i> — €${r.price}</div></div>`).join("");
}

async function searchName(){
  const name = document.getElementById("name").value.trim();
  const out = document.getElementById("name_results");
  out.innerHTML = "Searching...";
  const res = await fetch("/search/name", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({name: name})});
  const j = await res.json();
  if(j.error){ out.innerHTML = "<b>Error:</b> "+j.error; return; }
  if(!j.results || j.results.length===0){ out.innerHTML = "<i>No results</i>"; return; }
  out.innerHTML = j.results.map(r=>`<div class="result"><b>${r.name}</b><div>${r.description}</div><div><i>${r.category}</i> — €${r.price}</div></div>`).join("");
}

async function addProduct(){
  const name = document.getElementById("add_name").value.trim();
  const desc = document.getElementById("add_desc").value.trim();
  const cat = document.getElementById("add_cat").value.trim();
  const price = parseFloat(document.getElementById("add_price").value);
  const out = document.getElementById("add_result");
  out.innerHTML = "Adding...";
  const res = await fetch("/add", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({name, description: desc, category: cat, price})});
  const j = await res.json();
  if(j.error){ out.innerHTML = "<b>Error:</b> "+j.error; return; }
  out.innerHTML = "<b>Added product id:</b> "+j.id;
}