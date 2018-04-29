

var schemaHomeTemplate = _.template(
    '<a href="<%= project_url %>" class="list-group-item list-group-item-action flex-column align-items-start">' +
        '<div class="d-flex w-100 justify-content-between">' +
            '<h5 class="mb-1"><%= project_name %></h5>' +
            '<small>updated <%= project_last_update %></small>' +
        '</div>' +
        '<p class="mb-1"><%= project_description %> by <%= organization %></p>' +
    '</a>');
