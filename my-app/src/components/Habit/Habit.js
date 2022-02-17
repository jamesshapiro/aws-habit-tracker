import React, { Component } from 'react'
import ActivityCalendar from 'react-activity-calendar'
import { Amplify, Auth } from 'aws-amplify'

import sha256 from 'crypto-js/sha256'

const SCREEN_WIDTH = 850

class Habit extends Component {
  constructor(props) {
    super(props)
    this.state = {
      dataPoints: [],
      isMounted: false,
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

  // TODO: try this again with functional components
  // getCurrentUser = async () => {
  //   try {
  //     const user = await Auth.currentAuthenticatedUser()
  //     return user.attributes.email
  //   } catch (error) {
  //     return 'display'
  //   }
  // }

  getSquaresForUser = (user) => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const dd = String(tomorrow.getDate()).padStart(2, '0')
    const mm = String(tomorrow.getMonth() + 1).padStart(2, '0')
    const yyyy = tomorrow.getFullYear()
    const yyyymmdd = `${yyyy}-${mm}-${dd}`
    const numDaysToFetchFromDDB = 373
    var daysOfYear = this.getDaysOfYear(user, this.props.habitName)
    if (user !== 'display') {
      const username = user.attributes.email.replace('@', '%40')
      const token = user.signInUserSession.idToken.jwtToken
      const headers = {
        'Content-Type': 'application/json',
        Authorization: token,
      }
      var url =
        process.env.REACT_APP_GET_HABIT_DATA_AUTH_URL +
        `?user=${username}&PK1=${this.props.habitName}&limit=${numDaysToFetchFromDDB}&startkey=${yyyymmdd}`
      
      fetch(url, {
        method: 'GET',
        headers: headers
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
          dataItems.map((item) => {
            daysOfYear.forEach((dayOfYear) => {
              if (item.date === dayOfYear.date) {
                dayOfYear.count = item.count
                dayOfYear.level = item.level
              }
            })
          })
          const newState = { dataPoints: [...daysOfYear], isMounted: true }
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

  getTitle = (habitName) =>
    habitName.charAt(0).toUpperCase() + habitName.replaceAll('-', ' ').slice(1)

  render() {
    const numDaysToFetch = this.getNumDaysToFetch()
    const mytheme = this.props.habitName.toLowerCase().includes('github')
      ? {
          level0: '#EBEDF0',
          level1: '#9BE9A8',
          level2: '#40C463',
          level3: '#30A14E',
          level4: '#216E39',
        }
      : null

    return (
      <div className="habit">
        <h3 className="habit-title">{this.getTitle(this.props.habitName)}</h3>
        <div className="commit-graph">
          {this.state.isMounted && (
            <ActivityCalendar
              color={this.props.habitColor}
              data={this.state.dataPoints.slice(-numDaysToFetch, -1)}
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
              theme={mytheme}
            ></ActivityCalendar>
          )}
        </div>
      </div>
    )
  }
}

export default Habit