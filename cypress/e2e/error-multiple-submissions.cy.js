import './base.cy'

describe('Duplicated applications', () => {

  it('doesn\'t let you click on confirm multiple times', () => {
    cy.deleteAllApplications()
    cy.goToConfirmation(1);

    cy.get('#button-continue').as('submitButton');

    Cypress._.times(10, function () {
      cy.get('@submitButton').click({force: true});
    });
  });
})
