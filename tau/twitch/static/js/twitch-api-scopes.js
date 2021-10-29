let scopes = [];
let helixEndpoints = [];
let eventSubSubscriptions = [];
let endpointsByScope = {};
let useIrc = false;


window.onload = (event) => {
    ajaxGet(`${protocol}//${host}${port}/api/v1/twitch/eventsub-subscriptions`).subscribe(resp => {
        eventSubSubscriptions = resp;
        updateSubsForm();
    });

    ajaxGet(`${protocol}//${host}${port}/api/v1/twitch/scopes/`).subscribe(resp => {
        scopes = resp;
        ajaxGet(`${protocol}//${host}${port}/api/v1/twitch/helix-endpoints/`).subscribe(resp => {
            helixEndpoints = resp;
            updateScopesForm();
        });
    });
    ajaxGet(`${protocol}//${host}${port}/api/v1/settings/use_irc`).subscribe(resp => {
        useIrc = resp.use_irc;
        updateSettingsForm();
    })
}

function updateSettingsForm() {
    document.getElementById("use-irc").checked=useIrc;
}

function onTauFormSubmit() {
    useIrc = document.getElementById("use-irc").checked
    const payload = {
        value: useIrc
    };

    const sub = ajaxPut(`${protocol}//${host}${port}/api/v1/settings/use_irc`, payload).subscribe(resp => {
        
    });

    return false;
}

function updateSubsForm() {
    const table = document.createElement('table');
    table.setAttribute("class", "table table-striped")
    table.innerHTML = '<thead><tr><th></th><th>Name</th><th>Description</th></tr></thead>';
    const tableBody = document.createElement('tbody');
    eventSubSubscriptions.forEach(sub => {
        const row = createSubsFormRow(sub);
        tableBody.appendChild(row);
    });
    table.appendChild(tableBody);
    const form = document.getElementById('subs-form');
    console.log(form);
    form.appendChild(table);
    const submit = document.createElement('input');
    submit.setAttribute("type", "submit");
    submit.setAttribute("class", "btn btn-primary");
    submit.setAttribute("value", "Update Token")
    form.appendChild(submit);
}

function createSubsFormRow(sub) {
    const e = document.createElement('tr');
    const html = `<td><input ${sub.active ? 'checked' : null} type='checkbox' id='${sub.id}'></input></td><td>${sub.subscription_type}</td><td>${sub.description}</td>`
    e.innerHTML = html;
    return e;
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

function onSubsFormSubmit() {
    const subsEdited = eventSubSubscriptions.map(sub => {
        const checkbox = document.getElementById(sub.id);
        return {
            id: sub.id,
            active: checkbox.checked
        };
    });

    const sub = ajaxPut(`${protocol}//${host}${port}/api/v1/twitch/eventsub-subscriptions/bulk-activate`, subsEdited).subscribe(resp => {
        window.location.href = '/refresh-token-scope/';
    });
    return false;
}
