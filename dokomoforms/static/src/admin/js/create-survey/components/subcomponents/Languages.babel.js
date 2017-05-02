export default function Languages(props){

    const languages = props.languages;

    function languageList(languages){
        return props.languages.map(function(language){
            console.log('language', language)
            return (
                <option key={language} value={language}>{language}</option>
            )
        })
    }

    function languageHandler(event) {
        if (!event.target.value.length) return;
        console.log('handling', event.target.value)
        const newLang = event.target.value;
        event.target.value = '';
        props.addLanguage(newLang);
    }

    return (
        <div>
            <div className="form-group row survey-group">
                <label htmlFor="survey-title" className="col-xs-4 col-form-label survey-label">Languages: </label>
                <div className="col-xs-12">
                    <div>
                        Add Language: <input type="text" onBlur={languageHandler}/>
                    </div>
                    <div>
                        Default Language:
                        <select onChange={props.updateDefault}>
                            {languageList()}
                        </select>
                    </div>
                </div>
            </div>
        </div>
    )
}