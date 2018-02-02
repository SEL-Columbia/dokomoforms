var React = require('react'),
    createReactClass = require('create-react-class');

/*
 * Title component
 *
 * props:
 *  @title: Title text to render in content
 *  @message: 'hint' text to render in content
 */
module.exports = createReactClass({
    render: function() {
        return (
            <div className="content-padded">
                <h3>{this.props.title}</h3>
                <p>{this.props.message}</p>
            </div>
        );
    }
});
