import React from 'react';

// A bucket is associated with a subsurvey

class Bucket extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            this.bucket_type = '';
            this.bucket = '';
        };
    }

    render() {
        return (
            <div>
            </div>
        );
    }

}


// examples:

// {
//     bucket_type: 'multiple_choice',
//     bucket: {
//         'choice_number': 1
//     }
// }

// {
//     'bucket_type': 'integer',
//     'bucket': '[1, 3]',
// }

// {
//     'bucket_type': 'date',
//     'bucket': '[2015-01-01, 2015-02-01]',
// }

// {
//     'bucket_type': 'timestamp',
//     'bucket': (
//         '[2015-01-01 1:11, 2015-01-01 2:22]'
//     ),
// }