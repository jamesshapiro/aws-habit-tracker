import React, { Component } from 'react'
import GitHubCalendar from 'react-github-calendar'

class Github extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isMounted: false,
    }
  }
  getNewEntries = () => {
    var newState = { isMounted: true }
    this.setState(newState)
  }

  componentDidMount() {
    this.getNewEntries()
  }

  getTitle = () => {
    return "Commit to GitHub"
  }

  selectLastDays = (contributions) => {
    const today = new Date()
    const day = today.getDay()
    const numDaysToFetch = 365 + day
    const cutoff = new Date(today)
    cutoff.setDate(cutoff.getDate() - numDaysToFetch)
    const cutoff_dd = String(cutoff.getDate()).padStart(2, '0')
    const cutoff_mm = String(cutoff.getMonth() + 1).padStart(2, '0')
    const cutoff_yyyy = cutoff.getFullYear()
    console.log(`cutoff: ${cutoff_yyyy}-${cutoff_mm}-${cutoff_dd}`)

    contributions = contributions.map(item => {
      item.level = Math.min(item.count, 4)
      return item
    })

    return contributions.filter(day => {
      const date = new Date(day.date);
      const date_dd = String(date.getDate()).padStart(2, '0')
      const date_mm = String(date.getMonth() + 1).padStart(2, '0')
      const date_yyyy = date.getFullYear()
      return (
        date_yyyy > cutoff_yyyy ||
        (date_yyyy >= cutoff_yyyy && date_mm > cutoff_mm) ||
        (date_yyyy >= cutoff_yyyy && date_mm >= cutoff_mm && date_dd >= cutoff_dd)
      )
    });
  };

  render() {
    return (
      <div className="habit">
        <h3>{this.getTitle()}</h3>
        <div className="commit-graph">
          {this.state.isMounted && (
            <GitHubCalendar
              username="jamesshapiro"
              transformData={this.selectLastDays}
              showWeekdayLabels={true}
              hideTotalCount
              // hideColorLegend
            ></GitHubCalendar>
          )}
        </div>
      </div>
    )
  }
}

export default Github