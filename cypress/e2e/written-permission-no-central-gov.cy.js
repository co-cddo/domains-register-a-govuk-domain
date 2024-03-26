import './base.cy'

describe('Central-gov registrant scenario - Traverses to Written Permission page and selects No', () => {
  it('Central-gov registrant scenario - Traverses to Written Permission page and selects No', () => {
    cy.goToWrittenPermission()
    cy.selectYesOrNo('written_permission', 'no')

    //This message should be displayed for central-gov registrants
    cy.get('body').should('include.text', 'Chief Information Officer or equivalent you\’re applying on behalf of a central')
  })
})
