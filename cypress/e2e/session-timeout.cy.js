import './base.cy'

describe('session timeout tests', () => {

  beforeEach(()=>{
    cy.clock();
  });

  it('Displays the timeout warning after 15 minutes', () => {
    // go to RegistrantType page
    cy.goToRegistrantType()

    // check if model_dialog doesn't exist
    cy.get('#modal_dialog').should('not.be.visible');
    // clock tick
    cy.tick(15 * 60 * 1000);
    cy.get('#modal_dialog').should('exist');
    cy.get('#modal_dialog').should('be.visible');

  });

  it('Displays the timeout warning after 15 minutes and continue the session', () => {
    // go to RegistrantType page
    cy.goToRegistrantType()

    // clock tick
    cy.tick(15 * 60 * 1000);
    cy.get('#modal_dialog').should('exist');
    cy.get('#modal_dialog').should('be.visible');

    // Click the "Continue" button
    cy.get('#session-continue').click();

    // Check if the warning modal is hidden
    cy.get('#modal_dialog').should('not.be.visible');

  });

  it('Displays the timeout warning after 15 minutes and in 20 minutes session expires and goes to session-ended page', () => {
    // go to RegistrantType page
    cy.goToRegistrantType()

    // Simulate 15 minutes of inactivity
    cy.tick(15 * 60 * 1000);

    // Ensure the modal dialog exists and is visible
    cy.get('#modal_dialog').should('exist');
    cy.get('#modal_dialog').should('be.visible');

    // Simulate additional 5 minutes of inactivity
    cy.tick(5 * 60 * 1000);

    // Check if the warning modal is still hidden
    cy.get('#modal_dialog').should('not.be.visible');

    // Check if the user is not redirected to the session-ended page
    cy.url().should('include', '/session-ended/');

    // Check if the session-ended page Continue button takes us to registrar-details page
    cy.get('#id_submit').click();
    cy.url().should('include', '/registrar-details/');
  });
})
