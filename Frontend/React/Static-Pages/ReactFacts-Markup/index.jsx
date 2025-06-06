/*
Challenge: Starting from scratch, build and render the 
HTML for our section project. Check the Google slide for 
what you're trying to build.

We'll be adding more styling to it later.

Hints:
* The React logo is a file in the project tree, so you can
  access it by using `src="react-logo.png"` in your image
  element
* You can also set the `width` attribute of the image element
  just like in HTML. In the slide, I have it set to 40px
 */
import {createRoot} from "react-dom/client"

const root = createRoot(document.getElementById("root"))

function ReactLogo(){
  return (<img src="react-logo.png" width="40px" />)
}
function FunFacts(){
  return (
    <>
      <h1>Fun Facts about React</h1>
      <ul>
        <li>Was first relaesed in 2013</li>
        <li>Was originally crated by Jordan Walke</li>
        <li>Has well over 100K stars on Github</li>
        <li>Is maintained by Meta</li>
        <li>Power thousands of enterprise apps, including mobile apps</li>
      </ul>
    </>
    
  )
}
root.render(
  <main>
      <ReactLogo />
      <FunFacts />
  </main>
)
