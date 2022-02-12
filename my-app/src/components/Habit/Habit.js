import React, { Component } from 'react'
import ActivityCalendar from 'react-activity-calendar'

class Habit extends Component {
  constructor(props) {
    super(props)
    this.state = {
      dataPoints: [],
      isMounted: false,
    }
  }
  getNewEntries = () => {
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    const day = today.getDay()
    const dd = String(tomorrow.getDate()).padStart(2, '0')
    const mm = String(tomorrow.getMonth() + 1).padStart(2, '0')
    const yyyy = tomorrow.getFullYear()
    const yyyymmdd = `${yyyy}-${mm}-${dd}`
    const numDaysToFetch = Math.min(window.screen.width,window.innerWidth) > 650 ? 365 + day : 120 + day
    var url =
      process.env.REACT_APP_GET_HABIT_DATA_URL +
      `?PK1=${this.props.habitName}&limit=${numDaysToFetch}&startkey=${yyyymmdd}`
    fetch(url, {
      method: 'GET',
    })
      .then((response) => response.json())
      .then((data) => {
        const dataItems = data.Items.map((item) => (
           {
            count: parseInt(item.DATE_COUNT.S),
            date: item.SK1.S.slice(5),
            level: parseInt(item.DATE_LEVEL.S),
          }
      ))
        dataItems.reverse()
        const newState = { dataPoints: [...dataItems], isMounted: true }
        this.setState(newState)
      })
  }

  componentDidMount() {
    this.getNewEntries()
  }

  getTitle = (habitName) => habitName.charAt(0).toUpperCase() + habitName.replaceAll('-', ' ').slice(1)

  render() {
    return (
      <div className="habit">
        <h3>{this.getTitle(this.props.habitName)}</h3>
        <div className="commit-graph">
          {this.state.isMounted && (
            <ActivityCalendar
              color={this.props.habitColor}
              data={this.state.dataPoints}
              hideColorLegend={false}
              hideTotalCount={true}
              showWeekdayLabels={true}
              labels={{
                legend: {
                  less: 'Less',
                  more: 'More',
                },
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
                totalCount: '{{count}} days of 8+ hours sleep in {{year}}',
                weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
              }}
            ></ActivityCalendar>
          )}
        </div>
      </div>
    )
  }
}

export default Habit