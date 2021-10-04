var schemaHomeTemplate = _.template(
  '<a href="<%= url %>" aria-label="Read more about <%= name %>" class="list-group-item list-group-item-action flex-column align-items-start">' +
  '<div class="d-flex w-100 justify-content-between">' +
  '<h5 class="mb-1"><%= name %></h5>' +
  '<small>updated <%= last_update %></small>' +
  '</div>' +
  '<p class="mb-1 text-justify"><%= description %> by <%= organization %></p>' +
  '</a>');

var jsonObjectHomeTemplate = _.template(
  '<a href="<%= url %>" aria-label="Read more about <%= name %>" class="list-group-item list-group-item-action flex-column align-items-start">' +
  '<div class="d-flex w-100 justify-content-between">' +
  '<h5 class="mb-1"><%= name %></h5>' +
  '<small>updated <%= last_update %></small>' +
  '</div>' +
  '<p class="mb-1 text-justify"><%= description %> by <%= organization %></p>' +
  '</a>');

var collectionHomeTemplate = _.template(
  '<a href="<%= url %>" aria-label="Read more about <%= name %>" class="list-group-item list-group-item-action flex-column align-items-start">' +
  '<div class="d-flex w-100 justify-content-between">' +
  '<h5 class="mb-1"><%= name %></h5>' +
  '<small>updated <%= last_update %></small>' +
  '</div>' +
  '<p class="mb-1 text-justify"><%= description %></p>' +
  '</a>');

var badgeObjectFromCollection = _.template(
  '<span class="badge rounded-pill bg-success" title="<%= schema_name %>" object-id="<%= object_id %>"><%= name %> ' +
    '<a class="removeObject" role="button" title="Remove from collection" href="#">' +
      '<i class="fa fa-minus"></i>' +
    '</a>' +
  '</span>');
