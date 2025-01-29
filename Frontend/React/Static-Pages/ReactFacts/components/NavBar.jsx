/**
 * Challenge: complete the Navbar to match the Figma design
 * 
 * Hints:
 * - for semantic HTML purposes, the Navbar should render
 *   a <header> with a <nav> nested inside. The image and "ReactFacts"
 *   text elements can both be rendered as children inside the <nav>
 * - reference the Figma design for the most accurate info about
 *   colors, sizes, font information, etc.
 */
import logo from "../images/react-logo.png";
// import "./NavBar.css";
export default function NavBar(){
    return (
        <header>
          <nav className="navbar">
            <img src={logo} alt="React Logo" className="nav-logo" />
            <span className="nav-title">ReactFacts</span>
          </nav>
        </header>
      );
}
