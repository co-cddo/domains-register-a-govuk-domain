import './base.cy'

describe('Non-central-gov registrant scenario - Traverses to Written Permission page and selects No', () => {
    it('Non-central-gov registrant scenario - Traverses to Written Permission page and selects No', () => {
      cy.goToRegistrantType()
      cy.chooseRegistrantType(3)

      cy.typeInRegistrant()
      cy.checkPageTitleIncludes('Does your registrant have written permission to apply for a .gov.uk domain name?')

      cy.selectYesOrNo('written_permission', 'no')

      //This message should be displayed for non-central-gov registrants
      cy.get('body').should('include.text', 'Chief Executive if you\’re applying on behalf of any other public sector organisation')
    })
})
