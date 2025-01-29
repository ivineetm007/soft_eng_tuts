/**
 * Challenge: Build out the Entry component and render 1 instance of it
 * to the App
 * 
 * For now, just hard-code in the data, which you can find in
 * japan.md so you don't have to type it all out manually :)
 * 
 * Notes:
 * – Only render 1 instance of this Entry component for now
 * – I've pulled in marker.png for the little map marker icon
 *   that goes next to the location name
 * – The main purpose of this challenge is to show you where our limitations
 *   currently are, so don't worry about the fact that you're hard-coding all
 *   this data into the component.
 */
function Entry() {
    return (
        <article className="entry-container">
            <div className="entry-image-container">
                <img className="entry-image" src="https://scrimba.com/links/travel-journal-japan-image-url" alt="mount fuji" />
            </div>
            <div className="entry-content">
                <div className="entry-location">
                    <img src="../images/marker.png" className="entry-location-icon" />
                    <span className="entry-location-name">JAPAN</span>
                    <a
                        href="https://www.google.com/maps"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="entry-map-link"
                    >
                        View on Google Maps
                    </a>
                </div>
                <h1 className="entry-title">Mount Fuji</h1>
                <p className="entry-date">12 Jan, 2023 - 24 Jan, 2023</p>
                <p className="entry-description">
                    Mount Fuji is the tallest mountain in Japan, standing at 3,776 meters
                    (12,380 feet). Mount Fuji is the single most popular tourist site in
                    Japan, for both Japanese and foreign tourists.
                </p>
            </div>
        </article>
    );
}
export default Entry;