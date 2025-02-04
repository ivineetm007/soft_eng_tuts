1. Resuable Components and nesting of components.
2. JS inside JSX- Use curly braces `{}`. We can put any expression inside which returns some value. For example `return <h1> {new Date().getHours() % 12}</h1>`

## Props

1. Passing data into the component- Create a properties or prop for the component. FOr ex <Contact img="./images/mr-whiskerson.png" name="Mr. Whiskerson" phone="(212) 555-1234"/>
2. Desctructring props
3. Conditional rendering- ex `{props.setup && <p className="setup">Setup: {props.setup}</p>}`
4. Non-String props- Uaw basic js, ex `<Joke
            punchline="It's hard to explain puns to kleptomaniacs because they always take things literally."
            upvotes={10}
            isPun={true}
        />`

## Project

1. Design figma link: https://www.figma.com/design/QG4cOExkdbIbhSfWJhs2gs/Travel-Journal?node-id=0-1&p=f&t=d4Qr8y4mxE99klFD-0
