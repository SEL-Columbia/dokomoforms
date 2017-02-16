function Fields(props) {

    console.log('fields', props)
    return(
        <div className="fields">
            <div class="btn-group" role="group" aria-label="...">
              <button type="button" onClick={props.toggleField.bind(null, 'showHint')} className="btn btn-default">add hint</button>
              <button type="button" onClick={props.toggleField.bind(null, 'showLogic')} className="btn btn-default">add bounds</button>
              <button type="button" onClick={props.addSubSurvey} className="btn btn-default">add sub-survey</button>
              <button type="button" onClick={props.deleteNode} className="btn btn-default" id="delete-node">delete</button>
            </div>
        </div>
    )

}

export default Fields;