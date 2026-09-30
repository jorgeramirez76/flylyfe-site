/* Make direct links to FAQ answers useful without another click. */
(()=>{function reveal(){const id=location.hash.slice(1);const target=document.getElementById(id);if(target?.tagName==='DETAILS')target.open=true;}reveal();window.addEventListener('hashchange',reveal);})();
