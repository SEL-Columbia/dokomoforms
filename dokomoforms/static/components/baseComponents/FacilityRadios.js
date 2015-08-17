var React = require('react'); 

/*
 * Facility Radio component
 * Renders radio's specifically formatted for facility data
 *
 * props:
 *  @facilities: Array of facility objects (revisit format)
 *  @selectFunction: What to do when facility is selected
 *  @initValue: Default selected facility
 */ 
module.exports = React.createClass({
    /*
     * Keep track of which option is selected
     */
    getInitialState: function() {
        return {
            selected: this.props.initValue,
        }
    },

    /*
     * Make radio behave like single option checkbox
     * 
     * Calls selectFunction with option (passes null when option unchecked)
     *
     * @e: click event
     */
    onClick: function(e) {
        var option = e.target.value;
        var checked = e.target.checked;
        var selected = option;

        if (option === this.state.selected) {
            selected = null;
            checked = false;
        }

        e.target.checked = checked;
        window.etarget = e.target;
        //e.stopPropagation();
        //e.cancelBubble = true;

        console.log('selected', option, checked);
        if (this.props.selectFunction)
            this.props.selectFunction(selected);

        this.setState({
            selected: selected
        });
    },

    render: function() {
        var self = this;
        return (
                <div className='question__radios'>
                {this.props.facilities.map(function(facility) {
                    return (
                        <div
                                key={facility.uuid} 
                                className='question__radio noselect'
                        >

                            <input
                                type='radio' 
                                id={facility.uuid} 
                                name='facility' 
                                onClick={self.onClick} 
                                disabled={self.props.disabled}
                                defaultChecked={facility.uuid === self.state.selected}
                                value={facility.uuid}
                            />
                            <label 
                                htmlFor={facility.uuid} 
                                className='question__radio__label'
                            >
                                <span className="radio__span">
                                    <span></span>
                                </span>
                                <strong className='question__radio__strong__meta'>
                                    {facility.name}
                                </strong>
                            <br/>
                            <span className='question__radio__span__meta'>
                                {facility.properties.sector}
                            </span>
                            <span className='question__radio__span__meta'>
                                <em>{facility.distance && facility.distance.toFixed(2)}m</em>
                            </span>
                            </label>
                        </div>
                    ) 
                })}
                </div>
               )
    }
});

