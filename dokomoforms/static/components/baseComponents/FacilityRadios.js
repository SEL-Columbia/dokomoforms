var React = require('react'); 

/*
 * Facility Radio component
 * Renders radio's specifically formatted for facility data
 *
 * props:
 *  @facilities: Array of facility objects (revisit format)
 */ 
module.exports = React.createClass({
    render: function() {
        return (
                <div className='question__radios'>
                {this.props.facilities.map(function(facility) {
                    return (<div key={facility.value} className='question__radio'>
                            <input 
                                type='radio' 
                                id={facility.value} 
                                name='facility' 
                                value={facility.value}> 
                            </input>
                            <label htmlFor={facility.value} >
                            <span className="question__radio__span__btn"><span></span></span>
                                <strong>{facility.name}</strong>
                            </label>
                            <br/>
                            <span className='question__radio__span__meta'>
                                {facility.sector}
                            </span>
                            <span className='question__radio__span__meta'>
                                <em>{facility.distance}m</em>
                            </span>
                            </div>) 
                })}
                </div>
               )
    }
});

