<div class="btn-group">
    <button class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
        <span class="glyphicon glyphicon-cloud-download"></span> Download Data <span class="caret"></span>
    </button>
    <ul class="dropdown-menu dropdown-menu-right" role="menu">
        <li><a target="_blank" href="/api/v0/surveys/<%= data.survey_id %>/submissions">JSON</a></li>
        <li><a target="_blank" href="/api/v0/surveys/<%= data.survey_id %>/submissions?format=csv">CSV</a></li>
    </ul>
</div>
