import React, { useState } from 'react';

const CreateEvent = ({ createEvent }) => {
    const [eventName, setEventName] = useState('');
    const [eventDate, setEventDate] = useState('');
    const [eventLocation, setEventLocation] = useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        // Handle form submission logic here
        console.log('Event Name:', eventName);
        console.log('Event Date:', eventDate);
        console.log('Event Location:', eventLocation);
        // Call the createEvent function passed as a prop
        createEvent({ eventName, eventDate, eventLocation });
    }

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Event Name:</label>
                <input
                    type="text"
                    value={eventName}
                    onChange={(e) => setEventName(e.target.value)}
                    required
                />
            </div>
            <div>
                <label>Event Date:</label>
                <input
                    type="date"
                    value={eventDate}
                    onChange={(e) => setEventDate(e.target.value)}
                    required
                />
            </div>
            <div>
                <label>Event Location:</label>
                <input
                    type="text"
                    value={eventLocation}
                    onChange={(e) => setEventLocation(e.target.value)}
                    required
                />
            </div>
            <button type="submit">Create Event</button>
        </form>
    );

}

export default CreateEvent;