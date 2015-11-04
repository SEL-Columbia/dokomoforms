<tr class="submission-row btn-view-submission" data-id="<%= data.id %>">
    <td><%= data.submission_time %></td>
    <td><%= data.submitter_name %></td>
    <td><%= data._t(data.survey_title, data.survey_default_language) %></td>
</tr>
