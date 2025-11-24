

paginationContainer.innerHTML = "";



function createButton(label, page, disabled = false) {
    const button = document.createElement('button');
    button.textContent = label;
    if (disabled) button.disabled = true;
    button.addEventListener('click', () => {
        urlParams = new URLSearchParams(window.location.search)
        urlParams.set('page', page);
        window.location.search = urlParams.toString();
    });
    return button;
}




function createPagination(t, c, r=1){

    const totalpages = parseInt(t);
    if (totalpages <= 1) return;

    const currentpage = parseInt(c);
    const paginationContainer = document.getElementById('pagination');


    if (currentpage != 1) {
        paginationContainer.appendChild(createButton("≪", 1));
    }

    if (currentpage > 1) {
        paginationContainer.appendChild(createButton("<", currentpage - 1));
    }

    const range = r;
    const start = Math.max(1, currentpage - range);
    const end = Math.min(totalpages, currentpage + range);

    for (let i = start; i <= end; i++) {
        if (i === currentpage) {
            const input = document.createElement('input');
            input.type = "text";
            input.value = currentpage;
            input.style.width = "40px";
            input.addEventListener('input', () => {
                input.value = input.value.replace(/\D/g, '');
            });
            input.addEventListener('keydown', (e) => {
                if (e.key === "Enter") {
                    const val = parseInt(input.value);
                    if (!isNaN(val) && val >= 1 && val <= totalpages) {
                        urlParams = new URLSearchParams(window.location.search)
                        urlParams.set('page', val);
                        window.location.search = urlParams.toString();
                    }
                }
            });
            paginationContainer.appendChild(input);
        } else {
            const button = createButton(i, i);
            paginationContainer.appendChild(button);
        }
    }
    if (currentpage < totalpages) {
        paginationContainer.appendChild(createButton(">", currentpage + 1));
    }

    if (currentpage != totalpages) {
        paginationContainer.appendChild(createButton("≫", totalpages));
    }

}