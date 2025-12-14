import frappe
from conference_management_system.conference_management_system.utils.email_service import send_session_recommendations



class RecommendationEngine:
    
    @staticmethod
    def generate_recommendations(attendee_id, limit=5):
        """Generate session recommendations for an attendee"""
        try:
            # Get attendee's registration history
            registered_sessions = frappe.db.sql("""
                SELECT s.speaker, s.session_name, c.conference_name, s.name as session_id
                FROM `tabRegistration` r
                JOIN `tabSession` s ON r.session = s.name
                JOIN `tabConference` c ON s.conference = c.name
                WHERE r.attendee = %s
            """, attendee_id, as_dict=True)
            
            # Get attendee's preferences
            preferences = frappe.db.sql("""
                SELECT ap.session, ap.preference_type, s.speaker, s.session_name
                FROM `tabAttendee Preference` ap
                JOIN `tabSession` s ON ap.session = s.name
                WHERE ap.parent = %s AND ap.preference_type = 'Interested'
            """, attendee_id, as_dict=True)
            
            recommendations = []
            
            if registered_sessions or preferences:
                # Get speakers from history and preferences
                speakers = set()
                for session in registered_sessions:
                    if session.speaker:
                        speakers.add(session.speaker)
                
                for pref in preferences:
                    if pref.speaker:
                        speakers.add(pref.speaker)
                
                if speakers:
                    # Find sessions by same speakers
                    speaker_recommendations = frappe.db.sql("""
                        SELECT DISTINCT s.name, s.session_name, s.speaker, s.start_time, s.end_time, s.max_attendees,
                               c.conference_name, c.start_date
                        FROM `tabSession` s
                        JOIN `tabConference` c ON s.conference = c.name
                        WHERE s.speaker IN %s
                        AND c.status IN ('Upcoming', 'Ongoing')
                        AND s.name NOT IN (
                            SELECT session FROM `tabRegistration` WHERE attendee = %s
                        )
                        ORDER BY c.start_date ASC
                        LIMIT %s
                    """, (tuple(speakers), attendee_id, limit), as_dict=True)
                    
                    recommendations.extend(speaker_recommendations)
            
            # If not enough recommendations, add popular sessions
            if len(recommendations) < limit:
                popular_sessions = frappe.db.sql("""
                    SELECT s.name, s.session_name, s.speaker, s.start_time, s.end_time, s.max_attendees,
                           c.conference_name, c.start_date, COUNT(r.name) as registration_count
                    FROM `tabSession` s
                    JOIN `tabConference` c ON s.conference = c.name
                    LEFT JOIN `tabRegistration` r ON s.name = r.session
                    WHERE c.status IN ('Upcoming', 'Ongoing')
                    AND s.name NOT IN (
                        SELECT session FROM `tabRegistration` WHERE attendee = %s
                    )
                    GROUP BY s.name
                    ORDER BY registration_count DESC, c.start_date ASC
                    LIMIT %s
                """, (attendee_id, limit - len(recommendations)), as_dict=True)
                
                recommendations.extend(popular_sessions)
            
            # Add availability info for all recommendations
            for rec in recommendations:
                try:
                    registered_count = frappe.db.count("Registration", {"session": rec['name']})
                    max_attendees = rec.get('max_attendees', 0) or 0
                    rec['available_spots'] = max(0, max_attendees - registered_count)
                    rec['max_attendees'] = max_attendees
                except Exception:
                    rec['available_spots'] = 0
                    rec['max_attendees'] = 0
            
            return recommendations[:limit]
            
        except Exception as e:
            frappe.log_error(f"Error generating recommendations: {str(e)}", "Recommendation Engine")
            return []
    
    @staticmethod
    def send_weekly_recommendations():
        """Send weekly recommendations to all attendees (scheduled task)"""
        try:
            attendees = frappe.get_all("Attendee", 
                filters={"email_verified": 1},
                fields=["name", "email", "attendee_name"]
            )
            
            for attendee in attendees:
                recommendations = RecommendationEngine.generate_recommendations(attendee.name)
                if recommendations:
                    send_session_recommendations(attendee.email, recommendations)
                    
                    # Log the action
                    frappe.log_error(
                        f"Weekly recommendations sent to {attendee.email}",
                        "Recommendation Engine"
                    )
            
        except Exception as e:
            frappe.log_error(f"Error sending weekly recommendations: {str(e)}", "Recommendation Engine")
    
    @staticmethod
    def update_preferences_from_registration(registration_doc):
        """Auto-update attendee preferences based on registration"""
        try:
            attendee = frappe.get_doc("Attendee", registration_doc.attendee)
            session = frappe.get_doc("Session", registration_doc.session)
            
            # Check if preference already exists
            existing_pref = None
            for pref in attendee.preferences:
                if pref.session == session.name:
                    existing_pref = pref
                    break
            
            if existing_pref:
                existing_pref.preference_type = "Attended"
            else:
                attendee.append("preferences", {
                    "session": session.name,
                    "preference_type": "Attended"
                })
            
            attendee.save()
            
        except Exception as e:
            frappe.log_error(f"Error updating preferences: {str(e)}", "Recommendation Engine")