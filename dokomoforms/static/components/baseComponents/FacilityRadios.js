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
                    return (<div key={facility.uuid} className='question__radio'>
                            <input 
                                type='radio' 
                                id={facility.uuid} 
                                name='facility' 
                                value={facility.uuid}> 
                            </input>
                            <label htmlFor={facility.uuid} >
                            <span className="question__radio__span__btn"><span></span></span>
                                <strong>{facility.name}</strong>
                            </label>
                            <br/>
                            <span className='question__radio__span__meta'>
                                {facility.properties.sector}
                            </span>
                            <span className='question__radio__span__meta'>
                                <em>{facility.coordinates}m</em>
                            </span>
                            </div>) 
                })}
                </div>
               )
    }
});

