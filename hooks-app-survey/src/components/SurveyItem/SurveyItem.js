import React from 'react';

import styles from './SurveyItem.module.css';

function SurveyItem({ children, name, value, onChange }) {
  const handleRatingChange = (value) => {
    console.log(value)
    onChange(value);
  };
  return (
    <div>
      <div>{children.DISPLAY_NAME.S}</div>
        <fieldset className={styles.fieldsetStyle}>
          <legend>
            Select rating:
          </legend>
          
          {VALID_RATINGS.map(option => (
            <div key={option} className={styles.radioContainer}>
              <input
                type="radio"
                name={`current-rating-${name}`}
                id={`current-rating-${name}-${option}`}
                value={option}
                // checked={value === option}
                required
              />
              <label 
                htmlFor={option}
                onClick={() => handleRatingChange(option)}
              >
                {option}
              </label>
            </div>
          ))}
        </fieldset>
    </div>
  )
}

const VALID_RATINGS = ["1","2","3","4","5"];

export default SurveyItem;
