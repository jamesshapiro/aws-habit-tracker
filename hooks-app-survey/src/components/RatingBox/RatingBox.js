import React from 'react';
import * as style from './RatingBox.module.css';

const RATINGS = ['1', '2', '3', '4', '5'];

const RatingBox = ({ id, category, onRatingChange, attemptedSubmit }) => {
  const [selectedRating, setSelectedRating] = React.useState(null);

  const handleSelect = (rating) => {
    setSelectedRating(selectedRating === rating ? rating : rating);
    onRatingChange(id, rating);
  };

  return (
    <div>
      {/* <div className={`${styles.header} ${attemptedSubmit && selectedRating === null ? styles.headerError : ''}`}>{id+1}. {category}</div> */}
      <div className={`${style.header} ${attemptedSubmit && selectedRating === null ? style.headerError : ''}`}>{id+1}. {category}</div>
      <div className={style.boxContainer}>
        {RATINGS.map((rating) => (
          <div
            key={rating}
            onClick={() => handleSelect(rating)}
            className={`${style.box} ${selectedRating === rating ? style.selected : style.unselected}`}
          >
            {rating}
          </div>
        ))}
      </div>
      {attemptedSubmit && selectedRating === null && (
        <div className={`${style.notificationBox} ${style.notificationBoxShow}`}>
          Please select a rating.
        </div>
      )}
    </div>
  );
};

export default RatingBox;