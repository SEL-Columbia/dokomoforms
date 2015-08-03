var React = require('react'); 

/*
 * Facility Radio component
 * Renders radio's specifically formatted for facility data
 *
 * props:
 *  @facilities: Array of facility objects (revisit format)
 */ 
module.exports = React.createClass({
    getInitialState: function() {
        return {
            selected: null,
        }
    },
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
        if (this.props.onSelect)
            this.props.onSelect(option);

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
                        <div className='question__radio noselect'>
                            <input
                                type='radio' 
                                id={facility.uuid} 
                                name='facility' 
                                onClick={self.onClick} 
                                value={facility.uuid}> 
                            </input>
                            <label 
                                key={facility.uuid} 
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
                                <em>{facility.coordinates}m</em>
                            </span>
                            </label>
                        </div>
                    ) 
                })}
                </div>
               )
    }
});

