import React from 'react';
import styles from './RatingBox.module.css';

const RATINGS = ['1', '2', '3', '4', '5'];

const RatingBox = ({ id, category, onRatingChange, attemptedSubmit }) => {
  const [selectedRating, setSelectedRating] = React.useState(null);

  const handleSelect = (rating) => {
    setSelectedRating(selectedRating === rating ? rating : rating);
    onRatingChange(id, rating);
  };

  return (
    <div>
      <div className={`${styles.header} ${attemptedSubmit && selectedRating === null ? styles.headerError : ''}`}>{category}</div>
      <div className={styles.boxContainer}>
        {RATINGS.map((rating) => (
          <div
            key={rating}
            onClick={() => handleSelect(rating)}
            className={`${styles.box} ${selectedRating === rating ? styles.selected : styles.unselected}`}
          >
            {rating}
          </div>
        ))}
      </div>
      {attemptedSubmit && selectedRating === null && (
        <div className={`${styles.notificationBox} ${styles.notificationBoxShow}`}>
          Please select a rating.
        </div>
      )}
    </div>
  );
};

export default RatingBox;