module.exports = (function() {
    /**
     * Enable tooltips within the element defined by selector
     * @param  {String} selector [description]
     */

    let lastSurveyId = 1000;
    let lastNodeId = 0;
    let lastChoiceId = 100;

    function _addId(type) {
        let id = 0;
        if (type==='node') { id = ++lastNodeId; }
        if (type==='choice') { id = ++lastChoiceId; }
        if (type==='survey') { id = ++lastSurveyId; }
        return id;
    }

    function _checkIfEmpty(language, choices) {
        console.log('checking');
        choices.forEach(function(choice){
            if (choice[language].length===0) return true;
        })
        return false;
    }

    return {
        addId: _addId,
        checkIfEmpty: _checkIfEmpty
    };

})();