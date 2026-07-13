import React, { useState } from 'react';
import api from '../api';

const ListEvents = () => {
    const [events, setEvents] = useState([]);

    const fetchEvents = async () => {
        try {
            const response = await api.get('/events');
            setEvents(response.data);
        } catch (error) {
            console.error('Error fetching events:', error);
        }
    };
    
    const createEvent = async (eventData) => {
        try {
            await api.post('/events', eventData);
            fetchEvents(); // Refresh the list of events after creating a new one
        } catch (error) {
            console.error('Error creating event:', error);
        }
    };

};

export default ListEvents;