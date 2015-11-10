<div class="btn-group">
    <button class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
        View Translation <span class="caret"></span>
    </button>
    <ul class="dropdown-menu" role="menu">
        <!-- <li><a href="#">CSV (.csv)</a></li>
        <li><a href="#">KML (.kml)</a></li> -->
        <% for lang in survey.languages %>
            <li>
                <a href="#" class="survey-language" data-surveylang="<%= lang %>">
                <%= lang %>
                </a>
            </li>
        <% end %>
    </ul>
</div>
