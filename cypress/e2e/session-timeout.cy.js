import './base.cy'

describe('session timeout tests', () => {
  const FIFTEEN_MINUTES = 15 * 60 * 1000; // 15 minutes in milliseconds

  beforeEach(()=>{
    cy.clock();
  });

  it('displays the timeout warning after the preset duration', () => {
    // go to RegistrantType page
    cy.goToRegistrantType()

    // check if model_dialog doesn't exist
    cy.get('#timeout-warning-modal').should('not.be.visible');
    // clock tick
    cy.tick(FIFTEEN_MINUTES);
    cy.get('#timeout-warning-modal').should('exist');
    cy.get('#timeout-warning-modal').should('be.visible');

  });

  it('displays the timeout warning after the preset duration and continue the session', () => {
    // go to RegistrantType page
    cy.goToRegistrantType()

    // check if model_dialog doesn't exist
    cy.get('#timeout-warning-modal').should('not.be.visible');

    // clock tick
    cy.tick(FIFTEEN_MINUTES);
    cy.get('#timeout-warning-modal').should('exist');
    cy.get('#timeout-warning-modal').should('be.visible');

    // Click the "Continue" button
    cy.get('#session-continue').click();

    // Check if the warning modal is hidden
    cy.get('#timeout-warning-modal').should('not.be.visible');

  });

  it('displays the timeout warning after the preset duration and after time elapses session expires and goes to session-ended page', () => {
    // go to RegistrantType page
    cy.goToRegistrantType()

    // check if model_dialog doesn't exist
    cy.get('#timeout-warning-modal').should('not.be.visible');

    // Simulate 15 minutes of inactivity
    cy.tick(FIFTEEN_MINUTES);

    // Ensure the modal dialog exists and is visible
    cy.get('#timeout-warning-modal').should('exist');
    cy.get('#timeout-warning-modal').should('be.visible');

    // Simulate additional 5 minutes of inactivity
    cy.tick(5 * 60 * 1000);

    // Check if the warning modal is still hidden
    cy.get('#timeout-warning-modal').should('not.be.visible');

    // Check if the user is not redirected to the session-ended page
    cy.checkPageTitleIncludes('\n          Your session has ended due to inactivity\n        \n        You have been inactive for 15 minutes\n')

    // Check if the session-ended page Continue button takes us to registrar-details page
    cy.get('#id_submit').click();
    cy.checkPageTitleIncludes('Registrar details')
  });
})
