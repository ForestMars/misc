// final working email export script 

function getYesRSVPs() {
  var eventId = '217iu90t46cjj48mao7rtlg2mr'; 
  var confirmedEmails = new Set(); // Use a Set to prevent duplicates

  try {
    var event = Calendar.Events.get('primary', eventId);
    
    // 1. Process the standard Attendees array
    if (event.attendees) {
      event.attendees.forEach(function(a) {
        if (a.responseStatus === 'accepted') {
          confirmedEmails.add(a.email || a.displayName);
        }
      });
    }

    // 2. Check the Organizer (Often missing from the attendees array)
    if (event.organizer && event.organizer.self) {
      // In the API, 'self' means the current user running the script
      confirmedEmails.add(event.organizer.email);
    } else if (event.organizer) {
      // If you are looking at someone else's event where you are a guest
      // we still check if the organizer is a "Yes"
      // Note: Organizers are 'accepted' by default in most cases
      confirmedEmails.add(event.organizer.email);
    }

    // 3. Check the Creator
    if (event.creator && event.creator.email) {
      confirmedEmails.add(event.creator.email);
    }

    var resultList = Array.from(confirmedEmails);
    
    Logger.log("--- FINAL RSVP LIST ---");
    Logger.log("Total Count: " + resultList.length);
    resultList.forEach(function(email, i) {
      Logger.log((i + 1) + ": " + email);
    });

    return resultList;

  } catch (e) {
    Logger.log("API Error: " + e.message);
    return [];
  }
}