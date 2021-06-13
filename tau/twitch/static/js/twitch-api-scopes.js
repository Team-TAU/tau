let scopes = [];
let helixEndpoints = [];
let endpointsByScope = {};

window.onload = (event) => {
    ajaxGet(`${protocol}//${host}${port}/api/v1/twitch/scopes/`).subscribe(resp => {
        scopes = resp;
        ajaxGet(`${protocol}//${host}${port}/api/v1/twitch/helix-endpoints/`).subscribe(resp => {
            helixEndpoints = resp;
            updateScopesForm();
        });
    });
    
}

function updateScopesForm() {
    helixEndpoints.filter(endpoint => endpoint.scope).forEach(endpoint => {
        if(!(endpoint.scope in endpointsByScope)) {
            endpointsByScope[endpoint.scope] = [];
        }
        endpointsByScope[endpoint.scope].push(endpoint);
    });
    const table = document.createElement('table');
    table.innerHTML = '<thead><tr><th></th><th>Scope</th><th>Endpoints</th></tr></thead>';
    const tableBody = document.createElement('tbody');
    table.setAttribute("class", "table table-striped")
    scopes.forEach(scope => {
        const row = createFormRow(scope);
        tableBody.appendChild(row);
    });
    table.appendChild(tableBody);
    const form = document.getElementById('scope-form');
    form.appendChild(table);
    const submit = document.createElement('input');
    submit.setAttribute("type", "submit");
    submit.setAttribute("class", "btn btn-primary");
    submit.setAttribute("value", "Update Token")
    form.appendChild(submit);
}

function createFormRow(scope) {
    const e = document.createElement('tr');
    const endpoints = endpointsByScope[scope.id].map(endpoint => {
        return `<a href='${endpoint.reference_url}' target='_blank'>${endpoint.description}</a>`;
    }).join('<br>')
    const html = `<td><input ${scope.required ? 'checked' : null} type='checkbox' id='${scope.id}'></input></td><td>${scope.scope}</td><td>${endpoints}</td>`
    e.innerHTML = html;
    return e;
}

function onFormSubmit() {
    const scopesEdited = scopes.map(scope => {
        const checkbox = document.getElementById(scope.id);
        return {
            ...scope,
            required: checkbox.checked
        };
    });

    const sub = ajaxPut(`${protocol}//${host}${port}/api/v1/twitch/scopes/bulk/`, scopesEdited).subscribe(resp => {
        window.location.href='/refresh-token-scope/';
    });

    return false;
}
