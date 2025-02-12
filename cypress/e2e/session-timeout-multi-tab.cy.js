import './base.cy'

describe('session timeout tests multiple tabs', () => {

  beforeEach(()=>{
    cy.clock();
  });

  it('Tests redirection independently in two contexts', () => {
    // go to RegistrantType page
    cy.goToRegistrantType()

    cy.tick(20 * 60 * 1000);

    let firstContextUrl;
    cy.url().then((url) => {
      firstContextUrl = url;
      expect(firstContextUrl).contains('http://localhost:8010/'); // Ensure it hasn't redirected yet
    });

    // Open the second context (simulate a new tab by revisiting)
    // go to RegistrantType page
    cy.goToRegistrantType()

    let secondContextUrl;
    cy.url().then((url) => {
      secondContextUrl = url;
      expect(secondContextUrl).contains('http://localhost:8010/'); // Ensure it hasn't redirected yet
    });

    cy.tick(10 * 60 * 1000);

    // First tab should not timeout because second tab is open
    cy.wrap(null).then(() => {
      expect(firstContextUrl).contains('http://localhost:8010/');
    });

    // Second tab neither
    cy.url().then((url) => {
      expect(url).contains('http://localhost:8010/');
    });

    cy.tick(10 * 60 * 1000);

    cy.url().then((url) => {
      expect(url).to.equal('http://localhost:8010/session-ended/'); // second timeout timeouts after 20 seconds
    });

    cy.wrap(null).then(() => {
      expect(firstContextUrl).to.equal('http://localhost:8010/session-ended/'); // first tab should timeout, because second did
    });
  });
})
