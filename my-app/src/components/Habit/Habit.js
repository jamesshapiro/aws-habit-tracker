import React, { Component } from 'react'
import ActivityCalendar from 'react-activity-calendar'

class Habit extends Component {
    render() {
        return (
          <div className="habit">
            <h3>{this.props.habitName}</h3>
            <div className="commit-graph">
              <ActivityCalendar
                color="#0f6499"
                hideColorLegend="true"
                hideTotalCount="true"
                data={[
                  {
                    count: 2,
                    date: '2022-07-14',
                    level: 1,
                  },
                  {
                    count: 8,
                    date: '2022-07-15',
                    level: 4,
                  },
                  {
                    count: 0,
                    date: '2022-07-16',
                    level: 0,
                  },
                  {
                    count: 4,
                    date: '2022-07-17',
                    level: 2,
                  },
                  {
                    count: 0,
                    date: '2022-07-18',
                    level: 0,
                  },
                  {
                    count: 0,
                    date: '2022-07-19',
                    level: 0,
                  },
                  {
                    count: 6,
                    date: '2022-07-20',
                    level: 3,
                  },
                  {
                    count: 3,
                    date: '2022-07-21',
                    level: 2,
                  },
                  {
                    count: 8,
                    date: '2022-07-22',
                    level: 4,
                  },
                  {
                    count: 5,
                    date: '2022-07-23',
                    level: 2,
                  },
                  {
                    count: 0,
                    date: '2022-07-24',
                    level: 0,
                  },
                  {
                    count: 9,
                    date: '2022-07-25',
                    level: 4,
                  },
                  {
                    count: 2,
                    date: '2022-07-26',
                    level: 1,
                  },
                  {
                    count: 0,
                    date: '2022-07-27',
                    level: 0,
                  },
                  {
                    count: 0,
                    date: '2022-07-28',
                    level: 0,
                  },
                  {
                    count: 0,
                    date: '2022-07-29',
                    level: 0,
                  },
                  {
                    count: 2,
                    date: '2022-07-30',
                    level: 1,
                  },
                  {
                    count: 2,
                    date: '2022-07-31',
                    level: 1,
                  },
                  {
                    count: 3,
                    date: '2022-08-01',
                    level: 2,
                  },
                  {
                    count: 0,
                    date: '2022-08-02',
                    level: 0,
                  },
                  {
                    count: 6,
                    date: '2022-08-03',
                    level: 3,
                  },
                  {
                    count: 0,
                    date: '2022-08-04',
                    level: 0,
                  },
                  {
                    count: 0,
                    date: '2022-08-05',
                    level: 0,
                  },
                  {
                    count: 3,
                    date: '2022-08-06',
                    level: 2,
                  },
                  {
                    count: 2,
                    date: '2022-08-07',
                    level: 1,
                  },
                  {
                    count: 0,
                    date: '2022-08-08',
                    level: 0,
                  },
                  {
                    count: 0,
                    date: '2022-08-09',
                    level: 0,
                  },
                  {
                    count: 2,
                    date: '2022-08-10',
                    level: 1,
                  },
                  {
                    count: 9,
                    date: '2022-08-11',
                    level: 4,
                  },
                  {
                    count: 0,
                    date: '2022-08-12',
                    level: 0,
                  },
                  {
                    count: 4,
                    date: '2022-08-13',
                    level: 2,
                  },
                  {
                    count: 3,
                    date: '2022-08-14',
                    level: 2,
                  },
                  {
                    count: 4,
                    date: '2022-08-15',
                    level: 2,
                  },
                  {
                    count: 2,
                    date: '2022-08-16',
                    level: 1,
                  },
                  {
                    count: 2,
                    date: '2022-08-17',
                    level: 1,
                  },
                  {
                    count: 5,
                    date: '2022-08-18',
                    level: 2,
                  },
                  {
                    count: 1,
                    date: '2022-08-19',
                    level: 1,
                  },
                  {
                    count: 1,
                    date: '2022-08-20',
                    level: 1,
                  },
                  {
                    count: 0,
                    date: '2022-08-21',
                    level: 0,
                  },
                  {
                    count: 0,
                    date: '2022-08-22',
                    level: 0,
                  },
                  {
                    count: 0,
                    date: '2022-08-23',
                    level: 0,
                  },
                  {
                    count: 2,
                    date: '2022-08-24',
                    level: 1,
                  },
                  {
                    count: 3,
                    date: '2022-08-25',
                    level: 2,
                  },
                  {
                    count: 0,
                    date: '2022-08-26',
                    level: 0,
                  },
                  {
                    count: 2,
                    date: '2022-08-27',
                    level: 1,
                  },
                  {
                    count: 7,
                    date: '2022-08-28',
                    level: 3,
                  },
                  {
                    count: 0,
                    date: '2022-08-29',
                    level: 0,
                  },
                  {
                    count: 0,
                    date: '2022-08-30',
                    level: 0,
                  },
                  {
                    count: 6,
                    date: '2022-08-31',
                    level: 3,
                  },
                ]}
                labels={{
                  // legend: {
                  //   less: 'Less',
                  //   more: 'More',
                  // },
                  months: [
                    'Jan',
                    'Feb',
                    'Mar',
                    'Apr',
                    'May',
                    'Jun',
                    'Jul',
                    'Aug',
                    'Sep',
                    'Oct',
                    'Nov',
                    'Dec',
                  ],
                  // totalCount: '{{count}} contributions ON {{year}}',
                  weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                }}
              ></ActivityCalendar>
            </div>
          </div>
        )
    }
}

export default Habit