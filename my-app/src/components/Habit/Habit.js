import React, { Component } from 'react'
import ActivityCalendar from 'react-activity-calendar'
import { Auth } from 'aws-amplify'

import sha256 from 'crypto-js/sha256'

const SCREEN_WIDTH = 850

const colors = [
  '#b92514', // red
  '#2270A1', // blue
  '#315514', // green
]

class Habit extends Component {
  constructor(props) {
    super(props)
    this.state = {
      dataPoints: [],
      isMounted: false,
      abridgeLast: false,
    }
  }

  getNumDaysToFetch = () => {
    const dayOfWeekIdx = new Date().getDay()
    const numDaysToFetch =
      Math.min(window.screen.width, window.innerWidth) > SCREEN_WIDTH
        ? 365 + dayOfWeekIdx
        : 120 + dayOfWeekIdx
    return numDaysToFetch
  }

  getRandomDigitFromDateString = (dateString, habitName, user) => {
    if (user !== 'display') {
      return 0
    }
    const hashDigest = sha256(habitName + dateString)
    const lastDigit = Math.floor(Math.abs(hashDigest.words.pop() % 10) / 2)
    let secondToLastDigit = 0
    if (lastDigit === 0) {
      const otherDigit = Math.floor(
        Math.floor(Math.abs(hashDigest.words.pop() % 10) / 2)
      )
      if (otherDigit <= 2) {
        secondToLastDigit = otherDigit
      }
    }

    const result = Math.min(lastDigit + secondToLastDigit, 4)
    return result
  }

  getTodayDateString() {
    const today = new Date()
    const dd = String(today.getDate()).padStart(2, '0')
    const mm = String(today.getMonth() + 1).padStart(2, '0')
    const yyyy = today.getFullYear()
    return `${yyyy}-${mm}-${dd}`
  }

  getDaysOfYear = (user, habitName) => {
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    const dd = String(tomorrow.getDate()).padStart(2, '0')
    const mm = String(tomorrow.getMonth() + 1).padStart(2, '0')
    const yyyy = tomorrow.getFullYear()
    var daysOfYear = []

    for (
      var d = new Date(yyyy - 2, mm, dd);
      d <= today;
      d.setDate(d.getDate() + 1)
    ) {
      let dateCount = this.getRandomDigitFromDateString(
        `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(
          2,
          '0'
        )}-${String(d.getDate()).padStart(2, '0')}`,
        habitName,
        user
      )
      daysOfYear.push({
        count: dateCount,
        date: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(
          2,
          '0'
        )}-${String(d.getDate()).padStart(2, '0')}`,
        level: dateCount,
      })
    }
    return daysOfYear
  }

  getSquaresForUser = (user) => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const dd = String(tomorrow.getDate()).padStart(2, '0')
    const mm = String(tomorrow.getMonth() + 1).padStart(2, '0')
    const yyyy = tomorrow.getFullYear()
    const yyyymmdd = `${yyyy}-${mm}-${dd}`
    const numDaysToFetchFromDDB = 373
    var daysOfYear = this.getDaysOfYear(user, this.props.habit.habitName)
    if (user !== 'display') {
      const username = user.attributes.email.replace('@', '%40')
      const token = user.signInUserSession.idToken.jwtToken
      const headers = {
        'Content-Type': 'application/json',
        Authorization: token,
      }
      var url =
        process.env.REACT_APP_GET_HABIT_DATA_AUTH_URL +
        `?user=${username}&PK1=${this.props.habit.habitName}&limit=${numDaysToFetchFromDDB}&startkey=${yyyymmdd}`

      fetch(url, {
        method: 'GET',
        headers: headers,
      })
        .then((response) => response.json())
        .then((data) => {
          const dataItems = data.Items.map((item) => {
            return {
              count: parseInt(item.DATE_COUNT.S),
              date: item.SK1.S.slice(5),
              level: Math.min(parseInt(item.DATE_LEVEL.S), 4),
            }
          })
          let abridgeLast = true
          const todayDateString = this.getTodayDateString()
          dataItems.map((item) => {
            daysOfYear.forEach((dayOfYear) => {
              if (item.date === dayOfYear.date) {
                dayOfYear.count = item.count
                dayOfYear.level = item.level
              }
            })
          })
          dataItems.forEach((item) => {
            if (todayDateString === item.date) {
              abridgeLast = false
            }
          })
          const newState = {
            dataPoints: [...daysOfYear],
            isMounted: true,
            abridgeLast
          }
          // const newState = { dataPoints: [...daysOfYear], isMounted: true, abridgeLast }
          this.setState(newState)
        })
    } else {
      const newState = { dataPoints: [...daysOfYear], isMounted: true }
      this.setState(newState)
    }
  }

  getNewEntries = () => {
    Auth.currentAuthenticatedUser()
      .then((user) => {
        this.getSquaresForUser(user)
      })
      .catch((err) => {
        this.getSquaresForUser('display')
      })
  }

  resize = () => this.forceUpdate()

  componentDidMount() {
    window.addEventListener('resize', this.resize)
    this.getNewEntries()
  }

  getDayBefore(dateString) {
    const year = parseInt(dateString.slice(0, 4))
    const month = parseInt(dateString.slice(5, 7)) - 1
    const day = parseInt(dateString.slice(8))
    const eveOfStartDate = new Date(year, month, day)
    eveOfStartDate.setDate(eveOfStartDate.getDate() - 1)
    const dd = String(eveOfStartDate.getDate()).padStart(2, '0')
    const mm = String(eveOfStartDate.getMonth() + 1).padStart(2, '0')
    const yyyy = eveOfStartDate.getFullYear()
    return `${yyyy}-${mm}-${dd}`
  }

  componentDidUpdate(prevProps) {
    const dayBefore = this.getDayBefore(this.props.habit.habitCreationDate)
    if (prevProps) {
      const commitGraphId = document.getElementById(`habit-${this.props.idx}`)
      const rects = Array.from(commitGraphId.getElementsByTagName('rect'))
      rects.forEach((item) => {
        if (item.getAttribute('data-date') === dayBefore) {
          item.id = 'habit-start-date'
        }
      })
    }
  }

  render() {
    const numDaysToFetch = this.getNumDaysToFetch()
    const mytheme = this.props.habit.habitName.toLowerCase().includes('github')
      ? {
          level0: '#EBEDF0',
          level1: '#9BE9A8',
          level2: '#40C463',
          level3: '#30A14E',
          level4: '#216E39',
        }
      : null
    // TODO add timezone logic
    let daysToAbridge = this.state.abridgeLast ? 1 : 0
    return (
      <>
        {!this.props.habit.deletePlanned && (
          <div className="habit-container">
            <div className="habit">
              <div className="habit-title">
                {this.props.habit.habitDisplayName}
              </div>
              <div className="commit-graph" id={`habit-${this.props.idx}`}>
                {this.state.isMounted && (
                  <ActivityCalendar
                    color={
                      colors[
                        (this.props.idx - this.props.startIdx + colors.length) %
                          colors.length
                      ]
                    }
                    // to hide day-of, add -1 argument

                    data={
                      this.state.abridgeLast
                        ? this.state.dataPoints.slice(-numDaysToFetch, -1)
                        : this.state.dataPoints.slice(-numDaysToFetch)
                    }
                    //data={this.state.dataPoints.slice(-numDaysToFetch, -1)}
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
                      totalCount:
                        '{{count}} days of 8+ hours sleep in {{year}}',
                      weekdays: [
                        'Sun',
                        'Mon',
                        'Tue',
                        'Wed',
                        'Thu',
                        'Fri',
                        'Sat',
                      ],
                    }}
                    theme={mytheme}
                  ></ActivityCalendar>
                )}
              </div>
            </div>
          </div>
        )}
      </>
    )
  }
}

export default Habit