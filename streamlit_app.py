import json
from datetime import datetime, timedelta

import requests

import streamlit as st


def money_format(value):
    return f"{value:,.2f}"


def display_loan(loan):
    original_drawdown_date = datetime.fromtimestamp(int(loan["drawdownDate"]))
    currency = loan["liquidityAsset"]["symbol"]
    amount = (
        int(loan["amountFunded"]) / 1e6
        if currency == "USDC"
        else int(loan["amountFunded"]) / 1e18
    )
    pool = loan["fundingPool"]["poolName"]

    st.subheader(f"{money_format(amount)} {currency} " f"from {pool}")

    st.write(f"**Status:** {loan['state']}")
    st.write(f"**Initial Term:** {loan['initialTermDays']} days")
    st.write(f"**Current Term:** {loan['termDays']} days")
    st.write(f"**Term Start Date**: {original_drawdown_date.strftime('%B %d, %Y')}")
    st.write(
        f"**Initial Maturity Date**: {(original_drawdown_date + timedelta(days=int(loan['initialTermDays']))).strftime('%B %d, %Y')}"
    )
    st.write(
        f"**Current Maturity Date**: {datetime.fromtimestamp(int(loan['maturityDate'])).strftime('%B %d, %Y')}"
    )

    if loan["refinances"]:
        st.markdown("#### Refinancings")
    for refi in loan["refinances"]:
        refi_date = datetime.fromtimestamp(int(refi["deadline"]))
        st.write(f"**{refi_date.strftime('%B %d, %Y')}**")
        amount = (
            int(refi["principalOwed"]) / 1e6
            if currency == "USDC"
            else int(refi["principalOwed"]) / 1e18
        )
        st.write(f"**Amount**: {money_format(amount)} {currency}")

    etherscan_link = f"https://etherscan.io/address/{loan['id']}"
    st.markdown(f"[View on Etherscan]({etherscan_link})")


query = """query {
  loans(ethereumAddress: "0x07B6c7bC3d7dc0f36133b542eA51aA7Ac560E974") {
    id
    amountFunded
    claimableAmount
    collateralAmount
    collateralAsset {
      address
      symbol
      decimals
      price
    }
    collateralOffchain
    collateralRatio
    collateralRequired
    collateralSwapped
    createdAt
    debtLockerVersion
    defaultSuffered
    drawdownAmount
    drawdownAvailable
    drawdownDate
    endingPrincipal
    fundingDate
    fundingPool {
      poolName
      name
      amount
      companyName
    }
    fundsRedirected
    initialEndingPrincipal
    initialInterestRate
    initialRequestAmount
    initialTermDays
    interestPaid
    interestRate
    liquidationExcess
    liquidityAsset {
      address
      symbol
      decimals
      price
    }
    liquidityAssetReturned
    maturityDate
    nextPayment
    nextPaymentBreakdown {
      id
      principal
      interest
      delegateFee
      treasuryFee
      total
    }
    nextPaymentDue
    numLenders
    paymentIntervalDays
    paymentsRemaining
    paymentStructure
    poolDelegateFunding
    pools {
      id
      poolName
      name
      amount
      companyName
    }
    principalOwed
    purpose
    refinances {
      id
      calls
      status
      deadline
      updatedAt
      principalOwed
    }
    repossessed
    requestAmount
    startDate
    state
    termDays
    transaction {
      id
      timestamp
    }
    transactionHash
    treasuryFees
    updatedAt
    version
  }
}"""

url = "https://api.maple.finance/v1/graphql"
r = requests.post(url, json={"query": query})
raw_data = json.loads(r.text)
# st.json(raw_data)

loans = raw_data["data"]["loans"]
filtered = filter(lambda x: x["state"] not in ("Matured", "Expired", "Unfunded"), loans)

st.header("Auros Maple Loans")

for loan in filtered:
    display_loan(loan)
